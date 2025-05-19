"use client";

import PromptInput from "@/components/prompt-input";
import React, { useEffect, useState } from "react";
import { Button, Tooltip, ScrollShadow, cn, Select, SelectItem } from "@heroui/react";
import { Icon } from "@iconify/react";
import { MESSAGE_REVIEW, TPromptIdea } from "@/types";
import { useMainContext } from "@/components/context";
import { useClientApi } from "@/lib/hooks/useClientApi";
import { promptIdeasMock } from "@/mocks";
import axios from "axios";


const languages = [
    {
        title: "Русский",
        value: "ru"
    },
    {
        title: "Английский",
        value: "en"
    },
    {
        title: "Китайский",
        value: "cn"
    }
];
export type PromptInputWithBottomActionsProps = {promptIdeas: TPromptIdea[]}
export default function PromptInputWithBottomActions (props: PromptInputWithBottomActionsProps) {
    const { promptIdeas } = props;


    const {
        dialogueState,
        setDialogueState,
        prompt,
        setPrompt,
        questionId,
        sendPrompt,
        setQuestionId,
        promptIdeasNew,
        setPromptIdeas,
        selectedLanguage,
        setSelectedLanguage
    } = useMainContext();


    const { api } = useClientApi();
    useEffect(() => {
        api.get("/general/latest-questions").
            then((res) => {
                const newIdeas: TPromptIdea[] = [];
                for (const idea of res.data.latest) {
                    newIdeas.push({
                        title: idea,
                        prompt: idea,
                        description: ""
                    });
                }
                setPromptIdeas(newIdeas);
            }).
            catch((err) => {
                console.error(err);
            });
    }, []);


    const handleIdeaPress = (idea: TPromptIdea) => {
        setPrompt(idea.prompt);
    };

    return (
        <div className = "flex w-full flex-col gap-4">
            <ScrollShadow hideScrollBar className = "flex w-full flex-nowrap gap-2 overflow-x-scroll" orientation = "horizontal">
                <div className = "flex gap-2">
                    {promptIdeasNew.map((idea, index) => <Button onPress = {() => { handleIdeaPress(idea); }} key = {index} className = "flex h-14 flex-col items-start gap-0 bg-primary" variant = "flat">
                        <p>{idea.title}</p>
                        <p className = "text-default-500">{idea.description}</p>
                    </Button>)}
                </div>
            </ScrollShadow>
            <Select
                placeholder = {"Выберите язык ввода"}
                className = "w-[250px]"
                selectedKeys = {[selectedLanguage]}

                onSelectionChange = {(keys) => { setSelectedLanguage(Array.from(keys)[0]); }}
                classNames = {{ trigger: ["data-[hover=true]:bg-primary-dark", "bg-primary"] }}
            >
                {languages.map((language) => {
                    return <SelectItem title = {language.title} key = {language.value}/>;
                })}
            </Select>
            <form className = "flex w-full flex-col items-start rounded-medium bg-primary transition-colors hover:bg-primary-200/30">

                <PromptInput
                    classNames = {{
                        inputWrapper: "!bg-transparent shadow-none",
                        innerWrapper: "relative",
                        input: "pt-1 pl-2 pb-6 !pr-10 text-medium",
                    }}
                    endContent = {
                        <div className = "flex items-end gap-2">
                            <Tooltip showArrow content = "Отправить сообщение">
                                <Button
                                    isIconOnly
                                    color = {!prompt ? "default" : "secondary"}
                                    isDisabled = {!prompt}
                                    onPress = {sendPrompt}
                                    radius = "lg"
                                    size = "sm"
                                    variant = "solid"
                                >
                                    <Icon
                                        className = {cn("[&>path]:stroke-[2px]",
                                            !prompt ? "text-default-600" : "text-primary-foreground",)}
                                        icon = "solar:arrow-up-linear"
                                        width = {20}
                                    />
                                </Button>
                            </Tooltip>
                        </div>
                    }
                    minRows = {3}
                    radius = "lg"
                    value = {prompt}
                    variant = "flat"
                    onValueChange = {setPrompt}
                />
                <div className = "flex w-full items-center justify-between  gap-2 overflow-auto px-4 pb-4">
                    <div className = "flex w-full gap-1 md:gap-3">
                        <Button
                            size = "sm"
                            startContent = {
                                <Icon className = "text-default-500" icon = "solar:paperclip-linear" width = {18} />
                            }
                            variant = "flat"

                            className = "bg-primary-dark"
                        >
                            Прикрепить файл
                        </Button>
                        <Button
                            size = "sm"
                            startContent = {
                                <Icon className = "text-default-500" icon = "solar:soundwave-linear" width = {18} />
                            }
                            variant = "flat"
                            className = "bg-primary-dark"
                        >
                            Голосовое управление
                        </Button>
                    </div>
                    <p className = "py-1 text-tiny text-default-400">{prompt.length}/2000</p>
                </div>
            </form>
        </div>
    );
}
