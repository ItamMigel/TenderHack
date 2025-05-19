import { heroui } from "@heroui/react";


export const tailwindConfig = {
    content: [
        "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
        "./node_modules/@heroui/theme/dist/**/*.{js,ts,jsx,tsx}"
    ],
    theme: {
        screens: {
            sm: "640px",
            md: "1280px",
            lg: "1920px"
        },
        extend: {
            colors: {
                primary: {
                    DEFAULT: "#E7EEF7",
                    dark: "#D4DBE6"
                },
                secondary: "#264B82",
                text: {
                    black: "#1A1A1A",
                    gray: "#8C8C8C"
                }
            },
            fontFamily: { inter: ["Inter", "ui-serif", "Georgia"] }
        },

    },
    darkMode: "class",
    plugins: [heroui()]
};

export default tailwindConfig;
