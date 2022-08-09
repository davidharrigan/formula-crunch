import * as d3 from "d3";
import React, { useRef, useEffect, useState } from "react";

interface RankSliderProps {
  title: string;
  barData: {
    max: number;
    primary: DataProps[];
    secondary: DataProps[];
  };
}

interface DataProps {
  driverId: string;
  date: string;
  value: number;
}

interface Dimensions {
  width: number;
  height: number;
}

interface BarData {
  value: number;
  date: Date;
}

const useRefDimensions = (ref: React.RefObject<any>): Dimensions => {
  const [dimensions, setDimensions] = useState({ width: 1, height: 2 });
  React.useEffect(() => {
    if (ref.current) {
      const { current } = ref;
      const boundingRect = current.getBoundingClientRect();
      const { width, height } = boundingRect;
      setDimensions({ width: Math.round(width), height: Math.round(height) });
    }
  }, [ref]);
  return dimensions;
};

const RankSlider = (props: RankSliderProps) => {
  const ref = useRef(null);
  const dimensions = useRefDimensions(ref);
  const svgRef = useRef(null);

  useEffect(() => {
    draw();
  }, [props, dimensions]);

  const draw = () => {
    if (svgRef === null) {
      return;
    }

    drawBarGraph();
  };

  const drawBarGraph = () => {
    // draw bar data
    const { primary: barDataPrimary, secondary: barDataSecondary } =
      props.barData;
    let primary: Array<BarData> = [];
    let secondary: Array<BarData> = [];

    if (barDataPrimary) {
      primary = barDataPrimary.map((x) => {
        const date = d3.timeParse("%Y-%m-%d")(x.date);
        return { value: x.value, date: date ?? new Date() };
      });
    }
    if (barDataSecondary) {
      secondary = barDataSecondary.map((x) => {
        const date = d3.timeParse("%Y-%m-%d")(x.date);
        return { value: x.value, date: date ?? new Date() };
      });
    }

    const xScale = d3
      .scaleBand()
      .domain(d3.map(primary.concat(secondary), (d) => d.date.toString()))
      .range([0, dimensions.width]);
    const yScale = d3
      .scaleLinear()
      .domain([0, props.barData.max])
      .range([dimensions.height, dimensions.height / 2]);

    const primaryCanvas = d3
      .select(svgRef.current)
      .selectAll(`.primary-bar`)
      .data(primary);
    primaryCanvas
      .enter()
      .append("rect")
      .merge(primaryCanvas as any)
      .attr("class", "primary-bar")
      .attr("x", (d) => xScale(d.date.toString())!)
      .attr("y", (d) => yScale(d.value))
      .attr("width", xScale.bandwidth())
      .attr("height", (d) => {
        return dimensions.height - yScale(d.value) / 2;
      })
      .attr("fill", "white");
    primaryCanvas.exit().remove();

    const secondaryCanvas = d3
      .select(svgRef.current)
      .selectAll(`.secondary-bar`)
      .data(secondary);
    secondaryCanvas
      .enter()
      .append("rect")
      .merge(primaryCanvas as any)
      .attr("class", "primary-bar")
      .attr("x", (d) => xScale(d.date.toString())!)
      .attr("y", (d) => yScale(d.value))
      .attr("width", xScale.bandwidth())
      .attr("height", (d) => {
        return dimensions.height - yScale(d.value) / 2;
      })
      .attr("fill", "red");
    secondaryCanvas.exit().remove();
  };

  // const stuff = () => {
  //   const data = props.data.map((x) => {
  //     const date = d3.timeParse("%m/%d/%Y")(x.date);
  //     return { ...x, date };
  //   });

  //   const timeDomain = d3.extent(data, (d) => d.date);
  //   const xScale = d3
  //     .scaleTime()
  //     .range([0, dimensions.width])
  //     .domain(timeDomain);

  //   const tempMax = d3.max(data, (d) => d.high);
  //   const yScale = d3
  //     .scaleLinear()
  //     .range([0, dimensions.height])
  //     .domain([0, tempMax]);

  //   const canvas = d3.select(svgRef.current);
  //   const lows = canvas.selectAll(".lows").data([data]);

  //   lows
  //     .enter()
  //     .append("path")
  //     .attr("class", "lows")
  //     .merge(lows)
  //     .attr(
  //       "d",
  //       d3
  //         .line()
  //         .x((d) => xScale(d.date))
  //         .y((d) => yScale(d.low))
  //     )
  //     .attr("fill", "none")
  //     .attr("stroke", "white")
  //     .attr("stroke-width", 2);
  // };

  return (
    <div ref={ref} className="w-100">
      <svg width="100%" height="100%" ref={svgRef}></svg>
    </div>
  );
};

export default RankSlider;
