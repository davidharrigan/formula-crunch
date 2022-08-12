export interface DriverData {
  driverCode: string;
  driverColor: string;
  data: Telemetry[];
}

export type Telemetry = TrackData & {
  Speed: number;
  Distance: number;
  Brake: boolean;
  Throttle: number;
};

export type TrackData = {
  X: number;
  Y: number;
};
