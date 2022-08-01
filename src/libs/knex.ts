import knex from "knex";

export const getConnection = () => {
  return knex({
    client: "better-sqlite3",
    connection: {
      filename: "./data/db.sqlite"
    }
  })
}