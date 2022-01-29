const https = require("https");
const fs = require("fs");
const child_process = require("child_process");
const node_path = require("path");

if (process.argv.length !== 6){
    console.log(`Usage: node mac_publish.js <owner> <repo> <filePath> <fileName>`)
    process.exit(-1)
}

const owner = process.argv[2];
const repo = process.argv[3];
const localFilePath = process.argv[4];
const uploadedFileName = process.argv[5];

const getTag = () => {
    if (!fs.existsSync('desktop_client')) {
        console.log('desktop_client does not exist in the current working directory')
        process.exit(-1)
    } else {
        const package_json = fs.readFileSync("desktop_client/package.json")
        const parsed = JSON.parse(package_json.toString());
        return 'v' + parsed['version']
    }
}

const githubRequest = (method, path, data, filePath = null) => {
    return new Promise((resolve, reject) => {
        const req = https.request({
            hostname: (filePath) ? 'uploads.github.com' : 'api.github.com',
            path: path,
            method: method,
            headers: {
                'Accept': "application/vnd.github.v3+json",
                'Authorization': `token ${process.env.GITHUB_TOKEN}`,
                'User-Agent': repo,
            }
        }, res => {
            let out = "";
            res.on('data', (chunk) => {
                out += chunk;
            })
            res.on('end', () => {
                resolve({
                    statusCode: res.statusCode,
                    data: JSON.parse(out)
                });
            })
        })
        req.on('error', error => {
            reject(error)
        })
        if (filePath === null) {
            req.write(JSON.stringify(data));
        } else {
            const file = fs.readFileSync(filePath);
            const stats = fs.statSync(filePath);
            // const type = child_process.execSync(`file --mime-type -b ${filePath}`).toString().trim();

            req.setHeader("Content-Length", stats.size);
            req.setHeader("Content-Type", "application/octet-stream");
            req.path += `?name=${uploadedFileName}`

            req.write(file)
        }
        req.end();
    })
}

const getAllRelease = () => {
    console.log("Getting all releases...")
    return new Promise((resolve, reject) => {
        githubRequest('GET', `/repos/${owner}/${repo}/releases`, {
            "per_page": 100,
        }).then(resolve).catch(reject);
    })
}

const createRelease = () => {
    console.log("Creating release...")
    return new Promise((resolve, reject) => {
        githubRequest('POST', `/repos/${owner}/${repo}/releases`, {
            "tag_name": tag
        }).then(resolve).catch(reject);
    })
}

const setReleaseDraft = (releaseID) => {
    console.log(`Setting release ${releaseID} to draft...`)

    return new Promise((resolve, reject) => {
        githubRequest('POST', `/repos/${owner}/${repo}/releases/${releaseID}`, {
            "tag_name": tag,
            "name": tag,
            "draft": true
        }).then(resolve).catch(reject);
    })
}

const uploadAsset = (releaseID) => {
    return new Promise((resolve, reject) => {
        githubRequest('PATCH',
            `/repos/${owner}/${repo}/releases/${releaseID}/assets`,
            {},
            localFilePath)
            .then(resolve)
            .catch(reject);
    })
}

const tag = getTag();
getAllRelease().then(async ({statusCode: allReleaseStatusCode, data: allReleases}) => {
    if (allReleaseStatusCode !== 200) {
        // handle this
        console.log('getAllRelease failed:', allReleaseStatusCode);
    } else {
        let releaseID = null;
        let uploadURL = null;

        for (const release of allReleases) {
            if (release['name'] === tag) {
                releaseID = release['id'];
                uploadURL = release['upload_url']
                break;
            }
        }
        if (releaseID === null) {
            const {statusCode: newReleaseStatusCode, data: newRelease} = await createRelease();
            if (newReleaseStatusCode !== 201){
                // handle this
                console.log('createRelease failed:', newReleaseStatusCode)
            } else {
                releaseID = newRelease['id'];
                uploadURL = newRelease['upload_url']
            }
        }
        await setReleaseDraft(releaseID, tag);

        const uploadResult = await uploadAsset(releaseID).catch(error=>{
            console.log(error);
        });
        console.log(uploadResult);
    }

}).catch(error=>{
    console.log(error)
})


