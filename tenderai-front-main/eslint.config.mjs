import { fileURLToPath } from "url";
import * as path from "path";

import globals from "globals";
import pluginJs from "@eslint/js";
// import importPlugin from "eslint-plugin-import";
import { fixupPluginRules } from "@eslint/compat";
import { FlatCompat } from "@eslint/eslintrc";
import tailwind from "eslint-plugin-tailwindcss";
import eslintTs from "typescript-eslint";
import pluginReact from "eslint-plugin-react";
import stylisticJs from "@stylistic/eslint-plugin-js";


const project = "./tsconfig.json";
const filename = fileURLToPath(import.meta.url);
const dirname = path.dirname(filename);

const compat = new FlatCompat({
    baseDirectory: dirname,
    recommendedConfig: pluginJs.configs.recommended
});

function legacyPlugin (name, alias = name) {
    const plugin = compat.plugins(name)[0]?.plugins?.[alias];

    if (!plugin) {
        throw new Error(`Unable to resolve plugin ${name} and/or alias ${alias}`);
    }

    return fixupPluginRules(plugin);
}

/** @type {import('eslint').Linter.Config[]} */
export default eslintTs.config(
    pluginJs.configs.recommended,
    ...eslintTs.configs.recommended,
    ...compat.extends("plugin:import/typescript", "plugin:react-hooks/recommended", "plugin:import/recommended"),
    ...tailwind.configs["flat/recommended"],
    {
        files: ["**/*.{js,mjs,cjs,jsx,mjsx,ts,tsx,mtsx}"],
        ...pluginReact.configs.flat.recommended
    },
    {
        settings: {
            "import/extensions": [".js", ".jsx", ".ts", ".tsx", ""],
            "import/parsers": { "@typescript-eslint/parser": [".ts", ".tsx"] },
            "import/resolver": { node: { extensions: [".js", ".jsx", ".ts", ".tsx"] } }
        },
        plugins: { "@stylistic/js": stylisticJs },
        rules: {
            "@stylistic/js/array-element-newline": ["error", "consistent"],
            "@stylistic/js/brace-style": ["error", "stroustrup", { allowSingleLine: true }],
            "@stylistic/js/function-call-argument-newline": ["error", "consistent"],
            "@stylistic/js/function-paren-newline": ["error", { minItems: 4 }],
            "@stylistic/js/object-curly-spacing": ["error", "always"],
            "@stylistic/js/multiline-comment-style": ["error", "separate-lines"],
            "@stylistic/js/multiline-ternary": ["error", "always-multiline"],
            "@stylistic/js/object-curly-newline": ["error", { multiline: true }],
            "@stylistic/js/padded-blocks": ["error", "never"],
            "@stylistic/js/quote-props": ["error", "as-needed"],

            "@stylistic/js/array-bracket-newline": 2,
            "@stylistic/js/array-bracket-spacing": 2,
            "@stylistic/js/arrow-parens": 2,
            "@stylistic/js/arrow-spacing": 2,
            "@stylistic/js/block-spacing": 2,
            "@stylistic/js/comma-dangle": 0,
            "@stylistic/js/comma-spacing": 2,
            "@stylistic/js/comma-style": 2,
            "@stylistic/js/computed-property-spacing": 2,
            "@stylistic/js/dot-location": 2,
            "@stylistic/js/eol-last": 2,
            "@stylistic/js/function-call-spacing": 2,
            "@stylistic/js/generator-star-spacing": 2,
            "@stylistic/js/indent": ["error", 4],
            "@stylistic/js/implicit-arrow-linebreak": 2,
            "@stylistic/js/jsx-quotes": 2,
            "@stylistic/js/key-spacing": 2,
            "@stylistic/js/keyword-spacing": 2,
            "@stylistic/js/linebreak-style": 2,
            "@stylistic/js/lines-around-comment": 2,
            "@stylistic/js/lines-between-class-members": 2,
            "@stylistic/js/new-parens": 2,
            "@stylistic/js/newline-per-chained-call": 2,
            "@stylistic/js/no-confusing-arrow": 2,
            "@stylistic/js/no-extra-parens": 2,
            "@stylistic/js/no-extra-semi": 2,
            "@stylistic/js/no-floating-decimal": 2,
            "@stylistic/js/no-multi-spaces": 2,
            "@stylistic/js/no-multiple-empty-lines": 2,
            "@stylistic/js/no-trailing-spaces": 2,
            "@stylistic/js/no-whitespace-before-property": 2,
            "@stylistic/js/nonblock-statement-body-position": 2,
            "@stylistic/js/object-property-newline": 2,
            "@stylistic/js/one-var-declaration-per-line": 2,
            "@stylistic/js/operator-linebreak": 2,


            "@stylistic/js/padding-line-between-statements": 2,
            "@stylistic/js/quotes": 2,
            "@stylistic/js/rest-spread-spacing": 2,
            "@stylistic/js/semi": 2,
            "@stylistic/js/semi-spacing": 2,
            "@stylistic/js/semi-style": 2,
            "@stylistic/js/space-before-blocks": 2,
            "@stylistic/js/space-before-function-paren": 2,
            "@stylistic/js/space-in-parens": 2,
            "@stylistic/js/space-infix-ops": 2,
            "@stylistic/js/space-unary-ops": 2,
            "@stylistic/js/spaced-comment": 2,
            "@stylistic/js/switch-colon-spacing": 2,
            "@stylistic/js/template-curly-spacing": 2,
            "@stylistic/js/template-tag-spacing": 2,
            "@stylistic/js/wrap-iife": 2,
            "@stylistic/js/wrap-regex": 2,
            "@stylistic/js/yield-star-spacing": 2
        }
    },
    {
        rules: {
            "import/extensions": [
                "error",
                "ignorePackages",
                {
                    js: "never",
                    jsx: "never",
                    ts: "never",
                    tsx: "never",
                    "@": "never",
                    "": "never"
                }
            ],
            "import/order": [
                "error", {
                    groups: [
                    // Imports of builtins are first
                        "builtin",
                        // Then sibling and parent imports. They can be mingled together
                        ["sibling", "parent"],
                        // Then index file imports
                        "index",
                        // Then any arcane TypeScript imports
                        "object",
                    // Then the omitted imports: internal, external, type, unknown
                    ],
                }
            ],
            "no-console": 2,
            "react/jsx-equals-spacing": [
                2,
                "always"
            ],
            "react/jsx-uses-react": "error",
            "react/jsx-uses-vars": "error",
            "react/no-unescaped-entities": "off",
            "no-unused-vars": "warn",
            "@typescript-eslint/no-unused-vars": "warn",
            "import/no-dynamic-require": "warn",
            "import/no-nodejs-modules": "warn",
            "import/newline-after-import": [2, { count: 2 }],
            "no-empty": 1
        }
    },
    {

        ignores: [
            "node_modules/",
            ".next/"
        ],
        files: ["**/*.{js,jsx,mjs,cjs,ts,tsx}"],
        languageOptions: {
            globals: globals.browser,
            ecmaVersion: "latest",
            sourceType: "module",
            parserOptions: {
                project,
                tsconfigRootDir: import.meta.dirname,
                ecmaFeatures: { jsx: true },
                ecmaVersion: 12,
                sourceType: "module"
            }
        }
    }
);
