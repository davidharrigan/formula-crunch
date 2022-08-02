import { Knex } from "knex";
import moment from "moment";

export interface PitSummary {
  id: number;
  driverRaceSummaryId: string;
  average: string;
  totalTime: string;

  pitStops: Array<PitStop>
  fastestPitTime: string;
  fastestPitLap: number;
}

export interface PitStop {
  pitSummaryId: string;
  lapNumber: number;
  stop: number;
  duration: string;
}

export const getPitSummary = async (knex: Knex, raceSummaryId: number): Promise<PitSummary | null> => {
  const pitSummary = await knex
    .select<PitSummary>({
      id: "id",
      driverRaceSummaryId: "driver_race_summary_id",
      average: "average",
      totalTime: "total_time",
    })
    .from("pit_summary")
    .where({ driverRaceSummaryId: raceSummaryId })
    .first();
  if (!pitSummary) {
    return null;
  }

  const avg = moment(pitSummary.average);
  pitSummary.average = avg.format("ss.SSS");

  const total = moment(pitSummary.totalTime);
  pitSummary.totalTime = total.format("mm:ss.SSS");

  const pitStops = await knex
    .select<Array<PitStop>>({
      pitSummaryId: "pit_summary_id",
      lapNumber: "lap_number",
      stop: "stop",
      duration: "duration",
    })
    .from("pit_stop")
    .where({ pitSummaryId: pitSummary.id })

  if (pitStops.length > 0) {
    pitStops.forEach((v, idx) => {
      const dur = moment(v.duration)
      pitStops[idx].duration = dur.format("ss.SSS");
    })

    const sorted = pitStops.sort((a, b) => {
      if (a.duration < b.duration) return -1;
      else if (b.duration < a.duration) return 1;
      else return 0;
    })

    pitSummary.pitStops = pitStops;
    pitSummary.fastestPitLap = sorted[0].lapNumber;
    pitSummary.fastestPitTime = sorted[0].duration;
  }

  return pitSummary;
}