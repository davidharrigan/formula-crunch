import Driver from "../components/Driver";
import Stats from "../components/Stats";

const Instagram = () => {
  return (
    <div className="w-[1200px] h-[1200px] p-5 bg-oxfordBlue text-eggshell">
      <div className="flex flex-col gap-10">
        <div className="flex flex-row">
          <div className="basis-1/2">
            <Driver.Result
              name="Max Verstappen"
              subheading="2022 Austrian Grand Prix"
              place={2}
              image="drivers/Max.png"
              season={{ rank: 1, points: 208, wins: 6, podiums: 8 }}
            />
          </div>
          <div className="basis-1/2 px-16 mt-24">
            <Stats.RaceSummary
              startingGrid={1}
              time="1:24:25:844"
              tires={[
                { compound: "hard", laps: 22 },
                { compound: "hard", laps: 23 },
                { compound: "medium", laps: 13 },
              ]}
            />
          </div>
        </div>

        <div className="grid pt-4 px-16 grid-cols-2 gap-16">
          <Stats.Slider
            name="Fastest Lap"
            value="1:07.275"
            subtext="Lap 62"
            rank={1}
            totalParticipants={20}
          />
          <Stats.Slider
            name="Average Pace"
            value="1:07.275"
            rank={2}
            totalParticipants={20}
          />
          <Stats.Slider
            name="Fastest Pit"
            value="21.319"
            subtext="Lap 58"
            rank={4}
            totalParticipants={20}
          />
          <Stats.Slider
            name="Total Pit Time"
            value="1:04:785"
            rank={18}
            totalParticipants={20}
          />
          <Stats.Slider
            name="Overtakes"
            value="1"
            rank={18}
            totalParticipants={20}
          />
          <Stats.Slider
            name="Average Speed"
            value="217.777"
            subtext="kmh"
            rank={3}
            totalParticipants={20}
          />
          <Stats.Slider
            name="Fastest Speed Trap"
            value="325.5"
            subtext="kmh"
            rank={2}
            totalParticipants={20}
          />
        </div>
      </div>
    </div>
  );
};

export default Instagram;
