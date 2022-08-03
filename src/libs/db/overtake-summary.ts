import { Knex } from "knex";

export interface OvertakeSummary {
  driverRaceSummaryId: number;
  overtakes: number;
  overtakesRank: number
}

export const getOvertakeSummary = async (knex: Knex, raceId: number, raceSummaryId: number): Promise<OvertakeSummary | null> => {
  const overtakeSummary = await knex
    .select({
      driverRaceSummaryId: 'driver_race_summary_id',
      overtakes: 'overtakes_count',
      overtakesRank: 'overtakes_rank',
    })
    .from(
      knex
        .select('*')
        .rank('overtakes_rank', function () { this.orderBy('overtakes_count', 'desc') } )
        .from(knex
          .select('*')
          .count('*', {as: 'overtakes_count'})
          .from('overtake')
          .join("driver_race_summary", { "driver_race_summary.id": "overtake.driver_race_summary_id" })
          .where({ 'driver_race_summary.race_id': raceId })
            .andWhere(function () {
              this.andWhere(function () {
                this
                  .andWhere({ 'passing_status': 'OK' })
                  .andWhere({'passing_status_override': null})
              })
              .orWhere({ 'passing_status_override': 'OK' })
          })
        .groupBy('driver_race_summary_id')
      )
    )
    .where({ driverRaceSummaryId: raceSummaryId })
    .first()

  if (!overtakeSummary) {
    return {
      driverRaceSummaryId: raceSummaryId,
      overtakes: 0,
      overtakesRank: 20,
    }
  }

  return overtakeSummary;
}