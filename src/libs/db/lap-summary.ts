import { Knex } from "knex";
import moment from "moment";

export interface LapSummary {
  driverRaceSummaryId: number;
  fastestLap: number;
  fastestLapTime: string;
  fastestLapAverageSpeed: string;
  fastestLapSpeedTrap: string;
  averageTime: string;
  averageSpeed: string;
  fastestSpeedTrap: string;
}

export const getLapSummary = async (knex: Knex, raceSummaryId: number): Promise<LapSummary | null> => {
  const lapSummary = await knex
    .select({
      driverRaceSummaryId: "driver_race_summary_id",
      fastestLap: "fastest_lap",
      fastestLapTime: "fastest_lap_time",
      fastestLapAverageSpeed: "fastest_lap_average_speed",
      fastestLapSpeedTrap: "fastest_lap_speed_trap",
      averageTime: "average_time",
      averageSpeed: "average_speed",
      fastestSpeedTrap: "fastest_speed_trap",
    })
    .from<LapSummary>("lap_summary")
    .where({ driverRaceSummaryId: raceSummaryId })
    .first();
  if (!lapSummary) {
    return null;
  }

  // format data
  const fastestTime = moment(lapSummary.fastestLapTime);
  lapSummary.fastestLapTime = fastestTime.format("mm:ss.SSS");

  const avgTime = moment(lapSummary.averageTime);
  lapSummary.averageTime = avgTime.format("mm:ss.SSS");

  return lapSummary;
}