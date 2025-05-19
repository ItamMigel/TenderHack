"use client";
import StatsChip from "@/components/stats-chip";
import { useClientApi } from "@/lib/hooks/useClientApi";
import { chartMock, clustersMock, statsChipsMock } from "@/mocks";
import { Button } from "@heroui/react";
import ApexCharts from "apexcharts";
import dynamic from "next/dynamic";
import React, { useEffect, useRef, useState } from "react";


// const options: ApexCharts.ApexOptions = {
//     chart: {
//         type: "line",
//         height: 410,
//         toolbar: { show: false }
//     },
//     stroke: { curve: "smooth", },
//     ...chartMock
// };

const processClusterArray = (resData) => {
    const options = {
        chart: {
            type: "line",
            height: 410,
            toolbar: { show: false }
        },
        stroke: { curve: "smooth", },
        series: [],
        xaxis: { categories: ["00:00", "01:00", "02:00", "03:00", "04:00", "05:00", "06:00", "07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"] }

    };

    let reqAmount = 0;

    for (const cluster of resData) {
        const data = [];
        for (const dataPoint of cluster.data) {
            reqAmount += dataPoint.count;
            data.push({
                x: dataPoint.hour,
                y: dataPoint.count
            });
            // data.push({
            //     x: "23:00",
            //     y: dataPoint.count
            // });
        }
        options.series.push({
            name: cluster.title,
            color: cluster.color,
            data: data
        });
    }
    return {
        options,
        totalAmount: reqAmount
    };
};
const Chart = dynamic(() => import("@/components/chart"),
    { ssr: false });

export default function StatisticsPage () {
    const [chartOptions, setChartOptions] = useState({
        chart: {
            type: "line",
            height: 410,
            toolbar: { show: false }
        },
        stroke: { curve: "smooth", },
        ...chartMock
    });
    const [requestsState, setRequestsState] = useState({
        statsChip: statsChipsMock[0],
        chart: {
            chart: {
                type: "line",
                height: 410,
                toolbar: { show: false }
            },
            stroke: { curve: "smooth", },
            ...chartMock
        }
    });
    const [reviewsState, setReviewsState] = useState({
        statsChip: statsChipsMock[1],
        chart: {
            chart: {
                type: "line",
                height: 410,
                toolbar: { show: false }
            },
            stroke: { curve: "smooth", },
            ...chartMock
        }
    });


    const { api } = useClientApi();

    useEffect(() => {
        api.get("/statistics/24h").
            then((res) => {
                console.log(res.data);
                const options = {
                    chart: {
                        type: "line",
                        height: 410,
                        toolbar: { show: false }
                    },
                    stroke: { curve: "smooth", },
                    series: [],
                    xaxis: { categories: ["00:00", "01:00", "02:00", "03:00", "04:00", "05:00", "06:00", "07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"] }

                };

                const reqAmount = 0;

                const requestsProcessed = processClusterArray(res.data.requests);

                setRequestsState({
                    statsChip: {
                        title: "Запросов за сегодня",
                        value: requestsProcessed.totalAmount.toString(),
                        change: "0.2%",
                        changeType: "neutral",
                        iconUrl: "solar:users-group-rounded-linear",
                    },
                    chart: requestsProcessed.options
                });

                const reviewsProcessed = processClusterArray(res.data.reviews);

                setReviewsState({
                    statsChip: {
                        title: "Лайков за сегодня",
                        value: reviewsProcessed.totalAmount.toString(),
                        change: "52.3%",
                        changeType: "positive",
                        iconUrl: "solar:wallet-money-outline",
                    },
                    chart: reviewsProcessed.options
                });
            }).
            catch((err) => {});
    }, []);
    return <div className = "flex h-full flex-col overflow-y-auto pb-2 pt-12">
        <div>
            <div className = "text-[30px] font-bold leading-[36px]">Статистика и данные</div>
            <div className = "mb-6 text-[16px] leading-[24px] text-text-gray">Ознакомьтесь с вопросами</div>
        </div>

        <div className = "flex h-[155px] shrink-0 flex-nowrap gap-x-6 overflow-x-auto bg-transparent py-2">
            <div className = "h-[135px] w-[382px] shrink-0">
                <StatsChip stats = {requestsState.statsChip} onChartClick = {() => { setChartOptions(requestsState.chart); }}/>
            </div>
            <div className = "h-[135px] w-[382px] shrink-0">
                <StatsChip stats = {reviewsState.statsChip} onChartClick = {() => { setChartOptions(reviewsState.chart); }}/>
            </div>

            {/* {statsChipsMock.map((statsChip, index) => {
                return <div key = {index} className = "h-[135px] w-[382px] shrink-0">
                    <StatsChip stats = {statsChip}/>
                </div>;
            })} */}
        </div>

        <div className = "my-6 shrink-0 text-[18px] font-medium leading-[28px] text-[#3F3F46]">
            Отображение классов
        </div>
        {/* <div className = "mb-4 flex  max-w-full shrink-0 flex-nowrap gap-x-2 overflow-x-auto">
            {clustersMock.map((questionsCluster) => {
                return <Button
                    key = {questionsCluster.id}
                    size = "sm"
                    variant = "flat"
                    className = "rounded-[8px] px-2 py-1 text-[14px] font-medium leading-[20px] text-[#000000]"
                    style = {{ backgroundColor: questionsCluster.color }}
                >
                    {questionsCluster.title}
                </Button>;
            })}

        </div> */}

        <Chart options = {chartOptions}/>

    </div>;
}
