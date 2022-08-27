import Image from "next/image";

interface TireProps {
  compound: "WET" | "INTERMEDIATE" | "SOFT" | "MEDIUM" | "HARD";
  height: number;
  width: number;
}

const compoundMap = {
  SOFT: {
    alt: "soft-tyre",
    src: "/tires/soft.svg",
  },
  MEDIUM: {
    alt: "medium-tyre",
    src: "/tires/medium.svg",
  },
  HARD: {
    alt: "hard-tyre",
    src: "/tires/hard.svg",
  },
  INTERMEDIATE: {
    alt: "intermediate-tyre",
    src: "/tires/intermediate.svg",
  },
  WET: {
    alt: "wet-tyre",
    src: "/tires/wet.svg",
  },
};

const Tire = ({ compound, height = 90, width = 90 }: TireProps) => {
  const altSrc = compoundMap[compound];

  return (
    <Image alt={altSrc?.alt} width={width} height={height} src={altSrc?.src} />
  );
};

export default Tire;
