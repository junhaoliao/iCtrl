# Website

This website is built using [Docusaurus][docusaurus], a modern static website generator.

### Installation

```
$ npm install
```

### Local Development

```
$ npm run start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

### Build

```
$ npm run build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

### Deployment

This site is automatically deployed by [a GitHub workflow][deploy-github-pages] on every push to the `main` branch.

[docusaurus]: https://docusaurus.io/
[deploy-github-pages]: /.github/workflows/deploy-gh-pages.yaml
