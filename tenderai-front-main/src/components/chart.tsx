import React, { useEffect, useRef, useState } from "react";
import ApexCharts from "apexcharts";


export default function Chart (props: {options: object}) {
    const { options } = props;
    const chartWrapperRef = useRef(null!);
    const [chart, setChart] = useState<ApexCharts | null>(null);

    useEffect(() => {
        if (typeof window === "object") {
            const newChart = new ApexCharts(chartWrapperRef.current, options);

            setChart(newChart);

            newChart.render();

            return () => {
                if (typeof window === "object") {
                    newChart?.destroy();
                }
            };
        }
    }, [setChart, options]);

    return <div >
        <div ref = {chartWrapperRef}/>
    </div>;
}
