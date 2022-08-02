import { Knex } from "knex";
import moment from "moment";

export interface OvertakeSummary {
  numberOvertakes: number;
  overtakes: Array<Overtake>;
}

export interface Overtake {
  id: number;
  driverRaceSummaryId: number;
  time: string;
  lapNumber: number;
  position: number;
  passedDriverNumber: number; // TODO: use driver_id
  passingStatus: string | null;
  passingStatusOverride: string | null;
  passingStatusOverrideReason: string | null;
}

export const getOvertakeSummary = async (knex: Knex, raceSummaryId: number): Promise<OvertakeSummary | null> => {
  const overtakes = await knex
    .select<Array<Overtake>>({
      id: "id",
      driverRaceSummaryId: "driver_race_summary_id",
      time: "time",
      lapNumber: "lap_number",
      position: "position",
      passedDriverNumber: "passed_driver_id", // TODO: use driver_id
      passingStatus: "passing_status",
      passingStatusOverride: "passing_status_override",
      passingStatusOverrideReason: "passing_status_override_reason",
    })
    .from("overtake")
    .where({ driverRaceSummaryId: raceSummaryId })

  const overtakeSummary: OvertakeSummary = {
    numberOvertakes: 0,
    overtakes,
  };

  let numberOvertakes = 0
  overtakes.forEach(ov => {
    if (ov.passingStatusOverride !== null) {
      if (ov.passingStatusOverride === "OK") {
        numberOvertakes++;
      }
    } else if (ov.passingStatus === "OK") {
      numberOvertakes++;
    }
  })
  overtakeSummary.numberOvertakes = numberOvertakes;

  return overtakeSummary;
}