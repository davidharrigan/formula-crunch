import SoftTire from "../../assets/tires/soft.svg";
import MediumTire from "../../assets/tires/medium.svg";
import HardTire from "../../assets/tires/hard.svg";

interface TireProps {
  compound: "soft" | "medium" | "hard";
  laps: number;
}

const compoundMap = {
  soft: {
    alt: "soft-tyre",
    src: SoftTire,
  },
  medium: {
    alt: "medium-tyre",
    src: MediumTire,
  },
  hard: {
    alt: "hard-tyre",
    src: HardTire,
  },
};

const Tire = ({ compound, laps }: TireProps) => {
  const altSrc = compoundMap[compound];

  return (
    <div className="flex flex-col items-center gap-2">
      <div>
        <img alt={altSrc.alt} width="90px" src={altSrc.src} />
      </div>
      <div className="text-xl">{laps}</div>
    </div>
  );
};

export default Tire;
