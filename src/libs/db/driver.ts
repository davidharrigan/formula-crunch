import { Knex } from "knex";

export interface Driver {
  driverId: string;
  code: string;
  firstName: string;
  lastName: string;
}

export const getDriver = async (knex: Knex, driverId: string): Promise<Driver | null> => {
  const driver = await knex
    .select({
      driverId: "driver_id",
      code: "code",
      firstName: "first_name",
      lastName: "last_name",
    })
    .from("driver")
    .where({ driverId })
    .first();
  if (!driver) {
    return null;
  }

  return driver;
}