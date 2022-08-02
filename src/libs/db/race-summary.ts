import { Knex } from "knex";

export interface RaceSummary {
  id: number;
  driverId: string,
  raceId: number,
  gridPosition: number,
  position: number,
  seasonStanding: number,
  seasonPoints: number,
  status: string,
}

export const getRaceSummary = async (knex: Knex, driverId: string, circuitId: string, raceYear: string): Promise<RaceSummary | null> => {
  const raceSummary = await knex
    .select<RaceSummary>({
      id: "driver_race_summary.id",
      driverId: "driver_race_summary.driver_id",
      raceId: "driver_race_summary.race_id",
      gridPosition: "driver_race_summary.grid_position",
      position: "driver_race_summary.position",
      seasonStanding: "driver_race_summary.season_standing",
      seasonPoints: "driver_race_summary.season_points",
      status: "driver_race_summary.status",
    })
    .from("driver_race_summary")
    .where({
      "driver_race_summary.driver_id": driverId,
      "race.circuit_id": circuitId,
      "race.year": raceYear,
    })
    .join("race", { "race.id": "driver_race_summary.race_id" })
    .first();

  if (!raceSummary) {
    return null;
  }

  // format data
  raceSummary.position = parseInt(raceSummary.position as unknown as string)
  raceSummary.gridPosition = parseInt(raceSummary.gridPosition as unknown as string)
  raceSummary.seasonStanding = parseInt(raceSummary.seasonStanding as unknown as string)
  raceSummary.seasonPoints = parseInt(raceSummary.seasonPoints as unknown as string)

  return raceSummary;
}