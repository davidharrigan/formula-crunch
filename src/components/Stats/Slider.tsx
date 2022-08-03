import { SliderBar } from "./SliderBar";

interface SliderProps {
  name: string;
  value: string | number;
  subtext?: string;
  rank: number;
  totalParticipants: number;
}

const Slider = (props: SliderProps) => {
  const rankPercent =
    ((props.totalParticipants - (props.rank - 1)) / props.totalParticipants) *
    100;

  let sliderSection = 0;
  if (rankPercent <= 33.3) {
    sliderSection = 1;
  } else if (rankPercent <= 66.6) {
    sliderSection = 2;
  } else {
    sliderSection = 3;
  }

  return (
    <div className="flex flex-col gap-2">
      <div>
        <p className="text-3xl tracking-wide font-bold text-cyberYellow">
          {props.name}
        </p>
      </div>
      <div className="flex flex-row gap-4 items-end">
        <div>
          <p className="text-6xl font-bold tracking-wider">{props.value}</p>
        </div>
        <div>
          <p className="text-2xl text-bittersweet">{props.subtext}</p>
        </div>
      </div>

      {/* slider */}
      <div className="flex flex-row h-2 w-full mt-2 relative">
        <div
          style={{
            left: `${rankPercent}%`,
          }}
          className={`absolute -top-[0.3rem] bg-zinc-300 h-[1.2rem] w-[0.1rem] shadow-slider-gauge`}
        ></div>
        <SliderBar
          rank={sliderSection === 1 ? props.rank : undefined}
          color={sliderSection === 1 ? "red" : "light-gray"}
        />
        <SliderBar
          rank={sliderSection === 2 ? props.rank : undefined}
          color={sliderSection === 2 ? "yellow" : "dark-gray"}
        />
        <SliderBar
          rank={sliderSection === 3 ? props.rank : undefined}
          color={sliderSection === 3 ? "green" : "light-gray"}
        />
      </div>
    </div>
  );
};

export default Slider;
