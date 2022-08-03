import { Knex } from "knex";
import moment from "moment";

export interface PitSummary {
  id: number;
  driverRaceSummaryId: number;
  average: string;
  totalTime: string;

  avaerageRank: number;
  totalTimeRank: number;

  fastestPitTime: string;
  fastestPitLap: number;
  fastestPitRank: number;
}

export interface PitStop {
  pitSummaryId: string;
  lapNumber: number;
  stop: number;
  duration: string;
  durationRank: number;
}

export const getPitSummary = async (knex: Knex, raceId: number, raceSummaryId: number): Promise<PitSummary | null> => {
  const pitSummary = await knex
    .select<PitSummary>({
      id: "id",
      driverRaceSummaryId: "driver_race_summary_id",
      average: "average",
      totalTime: "total_time",
      averageRank: "average_rank",
      totalTimeRank: "total_time_rank"
    })
    .from(
      knex
        .select('*')
        .rank('average_rank', 'average')
        .rank('total_time_rank', 'total_time')
        .from(knex
          .select('*')
          .from('pit_summary')
          .join("driver_race_summary", { "driver_race_summary.id": "pit_summary.driver_race_summary_id" })
          .where({'driver_race_summary.race_id': raceId}).andWhereNot({'average': null}).andWhereNot({'total_time': null})
      )
    )
    .where({ driverRaceSummaryId: raceSummaryId })
    .first();
  if (!pitSummary) {
    return null;
  }

  const avg = moment(pitSummary.average);
  pitSummary.average = avg.format("ss.SSS");

  const total = moment(pitSummary.totalTime);
  pitSummary.totalTime = total.format("mm:ss.SSS");

  const fastestPitStop = await knex
    .select<PitStop>({
      pitSummaryId: "pit_summary_id",
      lapNumber: "lap_number",
      stop: "stop",
      duration: "duration",
      durationRank: "duration_rank",
    })
    .from(
      knex
        .select('*')
        .rank('duration_rank', 'fastest_pit_stop_duration')
        .from(knex
          .select('*')
          .min('duration', {as: 'fastest_pit_stop_duration'})
          .from('pit_stop')
          .join("pit_summary", { "pit_summary.id": "pit_stop.pit_summary_id" })
          .join("driver_race_summary", { "driver_race_summary.id": "pit_summary.driver_race_summary_id" })
          .where({'driver_race_summary.race_id': raceId})
          .groupBy('pit_summary_id')
        )
    )
    .where({ pitSummaryId: pitSummary.id })
    .first();

  if (fastestPitStop) {
    const fastest = moment(fastestPitStop.duration);
    pitSummary.fastestPitTime = fastest.format("mm:ss.SSS");
    pitSummary.fastestPitLap = fastestPitStop.lapNumber;
    pitSummary.fastestPitRank = fastestPitStop.durationRank;
  }

  return pitSummary;
}