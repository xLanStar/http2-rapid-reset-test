import fs from "node:fs";
import http2 from "node:http2";

const server = http2.createSecureServer({
  key: fs.readFileSync("localhost-privkey.pem"),
  cert: fs.readFileSync("localhost-cert.pem"),
});

server.on("stream", (stream, headers) => {
  // console.log(`stream ${stream.id} created`);
  // stream.on("close", () => console.log(`stream ${stream.id} closed`));
  stream.respond({
    ":status": 200,
  });
  stream.end();
});

server.on("error", (err) => console.error(err));

server.listen(3000);
console.log("Server started at port 3000");
