"use client";
import { useMainContext } from "./context";
import { Button, cn, Divider, Input, Modal, ModalBody, ModalContent, ModalHeader, Textarea } from "@heroui/react";
import { usePathname, useRouter } from "next/navigation";
import React, { useState } from "react";


const routes = [
    {
        title: "Главная",
        route: "/"
    },
    {
        title: "Чат",
        route: "/chat"
    },
    {
        title: "Ассистенты",
        route: "/assistants"
    },
    {
        title: "Вопросы",
        route: "/questions"
    },
    {
        title: "Статистика",
        route: "/stats"
    },

];
export default function Sidebar () {
    const pathname = usePathname();

    const router = useRouter();

    const {
        feedbackState,
        setFeedbackState
    } = useMainContext();

    return <div className = "flex h-full w-[289px] flex-col gap-y-6 overflow-hidden rounded-lg bg-primary p-6">
        <Modal isOpen = {feedbackState.isOpen} onOpenChange = {(isOpen) => { setFeedbackState((state) => { state.isOpen = isOpen; return { ...state }; }); }}>
            <ModalContent>
                {(onClose) => <>
                    <ModalHeader>
                        <div className = "w-full">
                            <div className = "mx-auto w-fit text-[20px] font-semibold leading-[28px]">
                                Напишите нам Ваш вопрос
                            </div>
                            <div className = "mx-auto w-fit text-[14px] font-normal leading-[20px] text-[#71717A]">
                                И мы ответим Вам в ближайшее время
                            </div>

                        </div>
                    </ModalHeader>
                    <ModalBody>
                        <div className = "space-y-2">
                            <Input
                                label = {"Почта"}
                                variant = "bordered"
                                className = ""
                                classNames = {{ inputWrapper: "bg-primary" }}

                            />
                            <Textarea
                                variant = "bordered"
                                classNames = {{ inputWrapper: "bg-primary" }}
                                placeholder = "Желательно, чтобы сюда вставлялся автоматом вопрос пользователя"
                                className = "min-h-[40px]"
                            />
                            <Divider orientation = "horizontal"/>

                            <div className = "flex w-full items-center justify-center gap-x-2 pb-3">
                                <Button
                                    color = "danger"
                                    variant = "flat"
                                    onPress = {() => { setFeedbackState((state) => { state.isOpen = false; return { ...state }; }); }}
                                >
                                    Отмена
                                </Button>
                                <Button
                                    color = "secondary"
                                    variant = "flat"
                                    onPress = {() => { setFeedbackState((state) => { state.isOpen = false; return { ...state }; }); }}
                                >
                                    Отправить
                                </Button>
                            </div>

                        </div>
                    </ModalBody>
                </>}
            </ModalContent>

        </Modal>
        <div>
            <img/>
            <span className = "text-[16px] font-bold ">14-Bit MISIS AI</span>
        </div>

        <div className = "mb-12 flex gap-3">
            <div>
                <img src = {"/uploads/users/user.png"} className = "size-10 rounded-full"/>
            </div>
            <div>
                <div className = "text-[14px] font-medium leading-[20px]">
                    Имя пользователя
                </div>
                <div className = "text-[12px] font-medium leading-4 text-text-gray">
                    Пользователь платформы
                </div>
            </div>
        </div>

        <div className = "space-y-[2px]">
            <div className = "text-[12px] font-medium leading-4 text-text-black">
                Overview
            </div>
            {routes.map((route) => {
                return <Button
                    key = {route.title}
                    onPress = {() => { router.push(route.route); }}
                    className = {cn("flex w-full items-center justify-start", pathname === route.route ? "bg-primary-dark" : "data-[hover=true]:bg-primary-dark")}
                    variant = {pathname === route.route ? "solid" : "light"}
                >
                    <div>{route.title}</div>

                    {/* {route.route === "/assistants" && */}
                    {/* // <Button className = "flex !size-[20px] min-w-0 items-center border border-[#71717A] px-0 pb-0.5 text-[20px] text-text-black" radius = "full">+</Button> */}
                    {/* } */}
                </Button>;
            })}

        </div>

        <div className = "flex flex-1 flex-col justify-end">
            <Button
                className = "flex w-full items-center justify-start"
                variant = "light"
                onPress = {() => { setFeedbackState((state) => { state.isOpen = true; return { ...state }; }); }}
            >
                <div>Подсказать идею</div>
            </Button>
            <Button
                className = "flex w-full items-center justify-start"
                variant = "light"
                onPress = {() => { router.push("/login"); }}
            >
                <div>Выйти</div>
            </Button>
        </div>
    </div>;
}
