import { Knex, knex } from "knex";

export const getConnection = (): Knex => {
  return knex({
    client: "sqlite3",
    connection: {
      filename: "./data/db.sqlite"
    },
    useNullAsDefault: true
  })
}