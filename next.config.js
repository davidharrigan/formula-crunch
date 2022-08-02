module.exports = {
  async redirects() {
    return [
      {
        source: "/",
        destination: "/races",
        permanent: false,
      },
    ];
  },
};
