"use client";
import { assistantsMock } from "@/mocks";
import { TAssistant } from "@/types";
import { Button } from "@heroui/react";
import React, { useEffect, useRef } from "react";


export default function AssistantsPage () {
    return <div className = "h-full max-w-[1330px] overflow-y-auto pb-2 pt-12">
        <div className = "flex w-full items-start justify-between">
            <div>
                <div className = "text-[30px] font-bold leading-[36px]">Список ассистентов</div>
                <div className = "mb-6 text-[16px] leading-[24px] text-text-gray">Создавайте и редактируйте</div>
            </div>
            <div>
                <Button className = "bg-primary">Новый ассистент</Button>
            </div>
        </div>
        <div className = "mx-auto flex flex-wrap justify-start gap-6">
            {[assistantsMock[0]].map((assistant) => {
                return (
                    <div key = {assistant.id} className = " h-[324px] w-[314px] overflow-hidden rounded-lg bg-[#FAFAFA] shadow-xl">
                        <div className = "h-[100px]" style = {{ background: `linear-gradient(${assistant.gradient})` }}>

                        </div>
                        <div className = "relative w-full pt-10">
                            <div className = "absolute left-1/2 top-0 h-[76px] w-[80px] -translate-x-1/2 -translate-y-1/2 rounded-full text-center">
                                <img src = {assistant.avatarUrl} className = "size-20"/>
                            </div>
                            <div className = " px-3">
                                <div className = "text-[18px] font-medium leading-[28px]">{assistant.title}</div>
                                <div className = "text-[14px] leading-[20px] text-text-gray ">{assistant.neuralNetworkTitle}</div>
                                <div className = "mb-1 mt-2 w-fit rounded-lg bg-primary p-1 text-[14px] leading-[20px]">{assistant.dataset.title}</div>
                            </div>
                            <div className = "flex flex-wrap gap-x-[7px] px-3">
                                {Object.keys(assistant.settings).map((settingKey) => {
                                    return <div key = {settingKey}>
                                        <span className = "text-[14px] font-medium leading-[20px] text-text-gray">{assistant.settings[settingKey]}</span>
                                        <span className = "text-[14px] leading-[20px] "> {settingKey}</span>
                                    </div>;
                                })}
                            </div>
                        </div>
                    </div>
                );
            })}

        </div>
    </div>;
}
