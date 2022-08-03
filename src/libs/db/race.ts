import { Knex } from "knex";

export interface Race {
  year: number;
  circuitId: string;
  roundNumber: number;
  eventName: string;
}

export const getRace = async (knex: Knex, raceId: number): Promise<Race | null> => {
  const race = await knex
    .select({
      year: "year",
      circuitId: "circuit_id",
      roundNumber: "round_number",
      eventName: "event_name",
    })
    .from("race")
    .where({
      id: raceId,
    })
    .first();

  if (!race) {
    return null;
  }

  return race;
}