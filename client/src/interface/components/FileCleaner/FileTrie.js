export class FileTrie {
  constructor(size) {
    // when it is non-zero, the base case is hit
    this.size = size;

    // recursively structure for insertion
    this.children = {};
  }

  insert(name, size) {
    // get parent name
    const slashIdx = name.indexOf('/');
    const parent = name.substring(0, slashIdx !== -1 ? slashIdx : undefined);

    // create entry if not exist
    if (!(parent in this.children)) {
      this.children[parent] = new FileTrie(0);
    }

    if (slashIdx === -1) {
      // "name" is already the base name
      this.children[parent].size = size;
    } else if (this.size===0){
      // keep inserting until no more parent in the "name"
      const rest = name.substring(slashIdx + 1);
      this.children[parent].insert(rest, size);
    }
  }

  count() {
    if (this.size !== 0) {
      // base case
      return this.size;
    }

    // if it has children, count the size of its children
    let total = 0;
    for (const c in this.children) {
      total += this.children[c].count();
    }

    return total;
  }
}
