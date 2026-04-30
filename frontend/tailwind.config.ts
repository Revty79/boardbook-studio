import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        boardbook: {
          cream: "#FFF7E8",
          sand: "#F3E4C7",
          ink: "#433124",
          mint: "#D7EFE2",
          peach: "#F7D8C2",
          sky: "#D3EAFD"
        }
      },
      boxShadow: {
        card: "0 12px 28px rgba(67, 49, 36, 0.12)"
      },
      borderRadius: {
        panel: "1rem"
      }
    }
  },
  plugins: []
};

export default config;
