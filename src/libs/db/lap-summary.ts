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

  fastestLapRank: number;
  averageTimeRank: number;
  fastestLapAverageSpeedRank: number;
  fastestLapSpeedTrapRank: number;
  averageSpeedRank: number;
  fastestSpeedTrapRank: number;
}

export const getLapSummary = async (knex: Knex, raceId: number, raceSummaryId: number): Promise<LapSummary | null> => {
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
      fastestLapRank: "fastest_lap_rank",
      averageTimeRank: "average_time_rank",
      fastestLapAverageSpeedRank: "fastest_lap_average_speed_rank",
      fastestLapSpeedTrapRank: "fastest_lap_speed_trap_rank",
      averageSpeedRank: "average_speed_rank",
      fastestSpeedTrapRank: "fastest_speed_trap_rank",
    })
    .from(
      knex
        .select('*')
        .rank('fastest_lap_rank', 'fastest_lap_time')
        .rank('average_time_rank', 'average_time')
        .rank('fastest_lap_average_speed_rank', function() { this.orderBy('fastest_lap_average_speed', 'desc') })
        .rank('fastest_lap_speed_trap_rank', function() { this.orderBy('fastest_lap_speed_trap', 'desc') })
        .rank('average_speed_rank', function() { this.orderBy('average_speed', 'desc') })
        .rank('fastest_speed_trap_rank', function() { this.orderBy('fastest_speed_trap', 'desc') })
        .from(knex
          .select('*')
          .from('lap_summary')
          .join("driver_race_summary", { "driver_race_summary.id": "lap_summary.driver_race_summary_id" })
          .where({'driver_race_summary.race_id': raceId})
        )
    )
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