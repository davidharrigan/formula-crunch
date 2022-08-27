import { StintSummary } from "components/Stats/StintSummary";
import { Knex } from "knex";
import moment from "moment";

export interface StintSummary {
  driverRaceSummaryId: number;
  stint: number;
  averageTime: string;
  lapCount: number;
  compound: "SOFT" | "MEDIUM" | "HARD" | "WET" | "INTERMEDIATE";
}

export const getStintSummary = async (
  knex: Knex,
  raceSummaryId: number
): Promise<StintSummary[]> => {
  const stintSummaries = await knex
    .select({
      driverRaceSummaryId: "driver_race_summary_id",
      stint: "stint",
      averageTime: "average_time",
      lapCount: "lap_count",
      compound: "compound",
    })
    .from("stint_summary")
    .where({ driverRaceSummaryId: raceSummaryId });
  if (!stintSummaries) {
    return [];
  }

  // format data
  return stintSummaries.map((s) => {
    const avgTime = moment(s.averageTime);
    s.averageTime = avgTime.format("mm:ss.SSS");
    return s;
  });
};
