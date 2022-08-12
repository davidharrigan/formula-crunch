import { TrackMap } from "components/_experimental/TrackMap";
import { CornerAnalysis } from "components/_experimental/CornerAnalysis";
import { NorrisData, RicciardoData } from "libs/data/mclaren";

export default function TrackMapExperiment() {
  return (
    <div className="bg-oxfordBlue w-screen h-full text-eggshell p-10">
      <div className="w-[600px] h-[600px]">
        <TrackMap
          driverData={[
            { driverCode: "NOR", driverColor: "#1E88E5", data: NorrisData },
            { driverCode: "RIC", driverColor: "#ffc107", data: RicciardoData },
          ]}
          color="#f1e9da"
          telemetryOverlay="fastest"
        />
      </div>
      <div className="pt-10">
        <CornerAnalysis
          turnNumber={1}
          driverData={[
            { driverCode: "NOR", driverColor: "#1E88E5", data: NorrisData },
            { driverCode: "RIC", driverColor: "#ffc107", data: RicciardoData },
          ]}
          distanceFrom={400}
          distanceTo={800}
        />
      </div>
    </div>
  );
}
