"use client";
import FeaturesCards from "@/components/features-cards";
import PromptInputWithBottomActions from "@/components/prompt-input-with-bottom-actions";
import React, { useContext, useState } from "react";
import Image from "next/image";
import { Avatar, Button, Divider, Input, Modal, ModalBody, ModalContent, ModalFooter, ModalHeader, Select, SelectItem, Slider, Textarea } from "@heroui/react";
import ChatMessages from "@/components/chat-messages";
import { chatMessagesMock, clustersMock, promptIdeasMock } from "@/mocks";
import { TAssistantSettings } from "@/types";
import FileInput from "@/components/file-input";
import { useMainContext } from "@/components/context";
import { useClientApi } from "@/lib/hooks/useClientApi";
import axios from "axios";


export default function ChatPage () {
    const [settings, setSettings] = useState<TAssistantSettings>({
        temperature: 0,
        maxLength: 0,
        topP: 0,
        frequencyPenalty: 0,
        presencePenalty: 0,
    });


    const [selectedDataset, setSelectedDataset] = useState("check");

    const [selectedModel, setSelectedModel] = useState("");


    const [datasetCreationState, setDatasetCreationSet] = useState({
        isModal: false,
        title: "",
        files: [],

    });

    const handleDatasetSelection = (keySet: Set<string>) => {
        const key = Array.from(keySet)[0];

        if (key === "create") {
            return;
        }

        setSelectedDataset(key);
    };

    const [clusterCreationState, setClusterCreationState] = useState({
        isModal: false,
        title: "",
        files: [],

    });

    const { api } = useClientApi();

    const handleClusterCreation = async () => {
        console.log(clusterCreationState);

        const formData = new FormData();

        formData.append("title", clusterCreationState.title);

        for (const file of clusterCreationState.files) {
            formData.append("files", file);
        }

        console.log(formData.getAll("files"));

        api.post("https://tenderai-api.foowe.ru/api/datasets/", formData).
            then((res) => {
                console.log(res);
            }).
            catch((err) => {
                console.log(err);
            });
    };


    const { dialogueState, setDialogueState } = useMainContext();
    return (
        <div className = "h-full overflow-y-auto pt-8">
            <div className = "flex h-full items-start gap-x-4">
                <Modal size = "sm" className = "min-h-[459px]" isOpen = {datasetCreationState.isModal} onOpenChange = {(isOpen) => {
                    if (!isOpen) {
                        setDatasetCreationSet({
                            isModal: false,
                            title: "",
                            files: []
                        });
                    }
                }}>
                    <ModalContent>
                        {(onClose) => <>
                            <ModalHeader>
                                <div className = "w-full pt-5">
                                    <div className = "text-[18px] font-medium leading-[28px]">
                                        Создание новой базы знаний
                                    </div>

                                </div>
                            </ModalHeader>
                            <ModalBody>
                                <div className = "space-y-2">
                                    <Divider orientation = "horizontal" className = "mb-3"/>
                                    <Input
                                        label = {"Название"}
                                        variant = "bordered"
                                        className = ""
                                        classNames = {{ inputWrapper: "bg-primary" }}
                                    />
                                    <div className = "text-[18px] font-medium leading-[28px]">
                                        Файлы для RAG системы
                                    </div>
                                    <FileInput/>

                                </div>
                            </ModalBody>
                            <ModalFooter>
                                <div className = "flex w-full items-center justify-end gap-x-2 pb-3">
                                    <Button
                                        variant = "bordered"
                                        onPress = {() => {
                                            setDatasetCreationSet({
                                                isModal: false,
                                                title: "",
                                                files: []
                                            });
                                        }}
                                    >
                                        Отмена
                                    </Button>
                                    <Button
                                        className = "bg-secondary text-white"
                                        onPress = {() => {
                                            setDatasetCreationSet({
                                                isModal: false,
                                                title: "",
                                                files: []
                                            });
                                        }}
                                    >
                                        Сохранить
                                    </Button>
                                </div>
                            </ModalFooter>
                        </>}
                    </ModalContent>

                </Modal>
                <Modal size = "sm" className = "min-h-[459px]" isOpen = {clusterCreationState.isModal} onOpenChange = {(isOpen) => {
                    if (!isOpen) {
                        setClusterCreationState({
                            isModal: false,
                            title: "",
                            files: []
                        });
                    }
                }}>
                    <ModalContent>
                        {(onClose) => <>
                            <ModalHeader>
                                <div className = "w-full pt-5">
                                    <div className = "text-[18px] font-medium leading-[28px]">
                                        Создание класса
                                    </div>

                                </div>
                            </ModalHeader>
                            <ModalBody>
                                <div className = "space-y-2">
                                    <Divider orientation = "horizontal" className = "mb-3"/>
                                    <Input
                                        label = {"Название"}
                                        variant = "bordered"
                                        className = ""
                                        onValueChange = {(newTitle) => {
                                            setClusterCreationState((state) => {
                                                state.title = newTitle;
                                                return state;
                                            });
                                        }}
                                        classNames = {{ inputWrapper: "bg-primary" }}
                                    />
                                    <div className = "text-[18px] font-medium leading-[28px]">
                                        Файлы для RAG системы
                                    </div>
                                    <FileInput onChange = {(files) => {
                                        setClusterCreationState((state) => {
                                            state.files = files;
                                            return { ...state };
                                        });
                                    }}/>

                                </div>
                            </ModalBody>
                            <ModalFooter>
                                <div className = "flex w-full items-center justify-end gap-x-2 pb-3">
                                    <Button
                                        variant = "bordered"
                                        onPress = {() => {
                                            setClusterCreationState({
                                                isModal: false,
                                                title: "",
                                                files: []
                                            });
                                        }}
                                    >
                                        Отмена
                                    </Button>
                                    <Button
                                        className = "bg-secondary text-white"
                                        onPress = {handleClusterCreation}
                                    >
                                        Сохранить
                                    </Button>
                                </div>
                            </ModalFooter>
                        </>}
                    </ModalContent>

                </Modal>
                <div className = "w-[280px] space-y-4">
                    <Select selectedKeys = {["check"]} label = "Модель">
                        <SelectItem key = {"check"} title = {"ChatGPT 4"}/>
                    </Select>
                    <Select selectedKeys = {[selectedDataset]} onSelectionChange = {handleDatasetSelection} label = "База Знаний">
                        <SelectItem key = {"check"} title = {"MandexMarketV1"} />
                        <SelectItem onPress = {() => {
                            setDatasetCreationSet({
                                isModal: true,
                                title: "",
                                files: []
                            });
                        }} key = {"create"}>
                            создать
                        </SelectItem>
                    </Select>

                    <Textarea label = "Дополнительная информация боту"/>

                    <Slider
                        label = "Температура"
                        defaultValue = {0.2}
                        maxValue = {1}
                        minValue = {0}
                        size = "sm"
                        step = {0.01}
                        classNames = {{ label: "text-text-black" }}
                        color = "secondary"
                    />
                    <Slider
                        label = "Максимальная длина"
                        defaultValue = {1024}
                        maxValue = {2048}
                        minValue = {512}
                        size = "sm"
                        classNames = {{ label: "text-text-black" }}
                        color = "secondary"
                        step = {1}
                    />
                    <Slider
                        label = "Топ P"
                        defaultValue = {0.5}
                        maxValue = {1}
                        minValue = {0}
                        size = "sm"
                        classNames = {{ label: "text-text-black" }}
                        color = "secondary"
                        step = {0.01}
                    />
                    <Slider
                        label = "Разнообразие текста"
                        defaultValue = {1}
                        maxValue = {2}
                        minValue = {0}
                        size = "sm"
                        classNames = {{ label: "text-text-black" }}
                        color = "secondary"
                        step = {0.01}
                    />
                    <Slider
                        label = "Работа с контекстом"
                        defaultValue = {1}
                        maxValue = {2}
                        minValue = {0}
                        size = "sm"
                        classNames = {{ label: "text-text-black" }}
                        color = "secondary"
                        step = {0.01}
                    />

                    <div className = "flex flex-wrap items-center gap-2">
                        {clustersMock.map((cluster, index) => {
                            return <div
                                key = {index}
                                className = "flex items-center gap-x-1 rounded-[8px] bg-[#D4D4D8]/40 px-2 py-1"
                            >
                                <div className = "size-[10px] rounded-full" style = {{ backgroundColor: cluster.color }}></div>
                                <div className = "text-[14px] font-medium leading-[20px]">
                                    {cluster.title}
                                </div>
                            </div>;
                        })}
                        <Button
                            onPress = {() => {
                                setClusterCreationState({
                                    isModal: true,
                                    title: "",
                                    files: []
                                });
                            }}
                            className = "flex !size-[20px] min-w-0 items-center border border-[#71717A] px-0 pb-0.5 text-[20px] text-text-black"
                            radius = "full"
                        >
                            +
                        </Button>
                    </div>

                </div>
                <div className = "h-full min-w-0 flex-1 pb-8">
                    <div className = "flex h-full flex-col justify-center gap-8">
                        <div className = "min-h-0 flex-1">
                            <ChatMessages messages = {dialogueState} isReviewClickable = {true}/>
                        </div>
                        <div className = "flex flex-col gap-2">
                            <PromptInputWithBottomActions promptIdeas = {promptIdeasMock}/>
                            <p className = "px-2 text-tiny text-default-400">
                                Искусственный интеллект иногда ошибается, будьте внимательный.
                            </p>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    );
}
