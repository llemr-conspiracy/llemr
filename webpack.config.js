const path = require("path");

module.exports = {
  entry: "./osler/assets/datadashboard/index.js", // path to our input file
  output: {
    filename: "datadashboard-imports.bundle.js", // output bundle file name
    path: path.resolve(__dirname, "./osler/static/js/datadashboard"), // path to our Django static directory
  },
};
