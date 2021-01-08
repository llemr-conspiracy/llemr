const path = require("path");

module.exports = {
  entry: "./osler/assets/index.js", // path to our input file
  output: {
    filename: "index-bundle.js", // output bundle file name
    path: path.resolve(__dirname, "./osler/static"), // path to our Django static directory
  },
};
