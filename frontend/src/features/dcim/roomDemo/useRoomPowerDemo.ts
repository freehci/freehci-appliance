import { useEffect, useState } from "react";

const LEN = 48;

export type RoomPowerDemo = {
  itKwHistory: number[];
  coolingKwHistory: number[];
  pueHistory: number[];
  upsSoc: number;
  itLoadKw: number;
  coolingKw: number;
  tempSupplyC: number;
  tempReturnC: number;
  humidityPct: number;
};

export function useRoomPowerDemo(roomId: number): RoomPowerDemo {
  const seed = roomId * 0.73;
  const [hist, setHist] = useState(() => ({
    it: Array.from({ length: LEN }, (_, i) => 10.5 + Math.sin(i * 0.11 + seed) * 2.1),
    cool: Array.from({ length: LEN }, (_, i) => 4.1 + Math.cos(i * 0.09 + seed) * 0.6),
    pue: Array.from({ length: LEN }, (_, i) => 1.27 + Math.sin(i * 0.07 + seed) * 0.025),
  }));
  const [live, setLive] = useState({
    upsSoc: 74,
    itLoadKw: 11,
    coolingKw: 4.2,
    tempSupplyC: 18,
    tempReturnC: 23,
    humidityPct: 44,
  });

  useEffect(() => {
    const id = window.setInterval(() => {
      const tt = Date.now() / 1000 + seed;
      const itLoadKw = 11 + Math.sin(tt * 0.33) * 2.5 + Math.sin(tt * 1.05) * 0.4;
      const coolingKw = 4.2 + Math.cos(tt * 0.29) * 0.95 + Math.sin(tt * 1.4) * 0.15;
      const pue = 1.28 + Math.sin(tt * 0.21) * 0.038;
      const upsSoc = 72 + Math.cos(tt * 0.19) * 11;
      const tempSupplyC = 17.6 + Math.sin(tt * 0.24) * 1.15;
      const tempReturnC = 22.8 + Math.sin(tt * 0.24) * 1.35;
      const humidityPct = 41 + Math.cos(tt * 0.16) * 6.5;

      setLive({ upsSoc, itLoadKw, coolingKw, tempSupplyC, tempReturnC, humidityPct });
      setHist((prev) => ({
        it: [...prev.it.slice(1), itLoadKw],
        cool: [...prev.cool.slice(1), coolingKw],
        pue: [...prev.pue.slice(1), pue],
      }));
    }, 900);
    return () => window.clearInterval(id);
  }, [seed]);

  return {
    itKwHistory: hist.it,
    coolingKwHistory: hist.cool,
    pueHistory: hist.pue,
    upsSoc: live.upsSoc,
    itLoadKw: live.itLoadKw,
    coolingKw: live.coolingKw,
    tempSupplyC: live.tempSupplyC,
    tempReturnC: live.tempReturnC,
    humidityPct: live.humidityPct,
  };
}
