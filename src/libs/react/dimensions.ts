import React, { useState } from "react";

export interface Dimensions {
  width: number;
  height: number;
}

export const useRefDimensions = (ref: React.RefObject<any>): Dimensions => {
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
