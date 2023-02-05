export default function handler(req, res) {
  const { query } = req.query;

  const { Client } = require("pg");
  const connectionString = process.env.PG_CONN_STRING;

  const client = new Client({
    connectionString,
  });
  client.connect();

  client.query(query, (err, dbRes) => {
    return res.send(dbRes);
    client.end();
  });
}
