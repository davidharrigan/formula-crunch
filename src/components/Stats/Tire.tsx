import Image from "next/image";

interface TireProps {
  compound: "soft" | "medium" | "hard";
  laps: number;
}

const compoundMap = {
  soft: {
    alt: "soft-tyre",
    src: "/tires/soft.svg",
  },
  medium: {
    alt: "medium-tyre",
    src: "/tires/medium.svg",
  },
  hard: {
    alt: "hard-tyre",
    src: "/tires/hard.svg",
  },
};

export const Tire = ({ compound, laps }: TireProps) => {
  const altSrc = compoundMap[compound];

  return (
    <div className="flex flex-col items-center gap-2">
      <div>
        <Image alt={altSrc.alt} width={90} height={90} src={altSrc.src} />
      </div>
      <div className="text-xl">{laps}</div>
    </div>
  );
};
