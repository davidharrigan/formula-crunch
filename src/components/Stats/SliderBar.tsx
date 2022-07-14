import { getOrdinal } from "../../libs/ordinal";

interface SliderBarProps {
  rank?: number;
  color: "dark-gray" | "light-gray" | "red" | "yellow" | "green";
}

export const SliderBar = ({ rank, color }: SliderBarProps) => {
  return (
    <div
      className={`basis-1/3
        ${color === "dark-gray" ? "bg-gray-500" : ""}
        ${color === "light-gray" ? "bg-gray-400" : ""}
        ${color === "green" ? "bg-emerald-500 shadow-slider" : ""}
        ${color === "yellow" ? "bg-amber-500 shadow-slider" : ""}
        ${color === "red" ? "bg-red-500 shadow-slider" : ""}`}
    >
      {rank && (
        <p
          className={`text-center pt-3 text-lg ordinal
          ${color === "green" ? "text-emerald-400" : ""}
          ${color === "yellow" ? "text-amber-400" : ""}
          ${color === "red" ? "text-red-400" : ""}`}
        >
          {getOrdinal(rank)}
        </p>
      )}
    </div>
  );
};
