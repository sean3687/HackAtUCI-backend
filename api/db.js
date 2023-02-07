// function insert(
//   floor_id,
//   comm,
//   term,
//   title,
//   price,
//   num_beds,
//   num_baths,
//   size,
//   img
// ) {
//   client.query(
//     "INSERT INTO housing VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
//     (floor_id, comm, term, title, price, num_beds, num_baths, size, img)
//   );
// }

// export default function handler(req, res) {
//   const { query } = req.query;

//   const { Client } = require("pg");
//   const connectionString = process.env.PG_CONN_STRING;

//   const client = new Client({
//     connectionString,
//   });

//   client.connect();
// client.query("DROP TABLE IF EXISTS housing");
// client.query(
//   "CREATE TABLE IF NOT EXISTS housing (id STRING PRIMARY KEY, community STRING NOT NULL, term STRING, title STRING, price INT NOT NULL, num_beds INT NOT NULL, num_baths DECIMAL NOT NULL, size INT NOT NULL, image STRING)"
// );

//   client.end();
//   client.query(query, (err, dbRes) => {
//     return res.send(dbRes);
//     client.end();
//   });
// }

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
