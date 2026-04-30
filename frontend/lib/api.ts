import {
  Character,
  CharacterReference,
  DashboardSummary,
  Generation,
  Project,
  ProjectDetail,
  StoryPage,
  StyleProfile
} from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";
const MEDIA_BASE = process.env.NEXT_PUBLIC_MEDIA_BASE_URL ?? "http://localhost:8000/media";

async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {})
    },
    cache: "no-store"
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || "Request failed");
  }

  return (await response.json()) as T;
}

async function apiFormRequest<T>(path: string, formData: FormData): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    body: formData,
    cache: "no-store"
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || "Upload failed");
  }

  return (await response.json()) as T;
}

export function mediaUrl(path: string) {
  return `${MEDIA_BASE}/${path}`;
}

export const api = {
  getDashboardSummary: () => apiRequest<DashboardSummary>("/dashboard/summary"),

  listProjects: () => apiRequest<Project[]>("/projects"),
  createProject: (payload: { title: string; description?: string }) =>
    apiRequest<Project>("/projects", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  getProject: (projectId: number) => apiRequest<ProjectDetail>(`/projects/${projectId}`),
  updateProject: (projectId: number, payload: { title?: string; description?: string }) =>
    apiRequest<Project>(`/projects/${projectId}`, {
      method: "PATCH",
      body: JSON.stringify(payload)
    }),

  listCharacters: (projectId: number) => apiRequest<Character[]>(`/projects/${projectId}/characters`),
  createCharacter: (
    projectId: number,
    payload: { name: string; description?: string; personality?: string; locked_traits: string[] }
  ) =>
    apiRequest<Character>(`/projects/${projectId}/characters`, {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  getCharacter: (projectId: number, characterId: number) =>
    apiRequest<Character>(`/projects/${projectId}/characters/${characterId}`),
  updateCharacter: (
    projectId: number,
    characterId: number,
    payload: { name?: string; description?: string; personality?: string; locked_traits?: string[] }
  ) =>
    apiRequest<Character>(`/projects/${projectId}/characters/${characterId}`, {
      method: "PATCH",
      body: JSON.stringify(payload)
    }),
  addCharacterReferencePath: (
    projectId: number,
    characterId: number,
    payload: { image_path: string; note?: string }
  ) =>
    apiRequest<CharacterReference>(`/projects/${projectId}/characters/${characterId}/references`, {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  uploadCharacterReference: (projectId: number, characterId: number, file: File, note?: string) => {
    const formData = new FormData();
    formData.append("file", file);
    if (note) {
      formData.append("note", note);
    }
    return apiFormRequest<CharacterReference>(
      `/projects/${projectId}/characters/${characterId}/references/upload`,
      formData
    );
  },

  getStyleProfile: (projectId: number) => apiRequest<StyleProfile>(`/projects/${projectId}/style-profile`),
  upsertStyleProfile: (
    projectId: number,
    payload: {
      visual_style: string;
      color_palette: string;
      lighting: string;
      composition: string;
      negative_prompt_rules: string;
    }
  ) =>
    apiRequest<StyleProfile>(`/projects/${projectId}/style-profile`, {
      method: "PUT",
      body: JSON.stringify(payload)
    }),

  listPages: (projectId: number) => apiRequest<StoryPage[]>(`/projects/${projectId}/pages`),
  createPage: (
    projectId: number,
    payload: { title: string; page_number: number; text_content: string }
  ) =>
    apiRequest<StoryPage>(`/projects/${projectId}/pages`, {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  getPage: (projectId: number, pageId: number) => apiRequest<StoryPage>(`/projects/${projectId}/pages/${pageId}`),
  updatePage: (
    projectId: number,
    pageId: number,
    payload: { title?: string; page_number?: number; text_content?: string }
  ) =>
    apiRequest<StoryPage>(`/projects/${projectId}/pages/${pageId}`, {
      method: "PATCH",
      body: JSON.stringify(payload)
    }),

  buildPrompt: (pageId: number) =>
    apiRequest<{ prompt: string; negative_prompt: string; seed: number | null }>("/generations/build-prompt", {
      method: "POST",
      body: JSON.stringify({ page_id: pageId })
    }),
  generateImage: (pageId: number) =>
    apiRequest<Generation>("/generations/generate", {
      method: "POST",
      body: JSON.stringify({ page_id: pageId })
    }),
  refineGeneration: (pageId: number, parentGenerationId: number, instruction: string) =>
    apiRequest<Generation>("/generations/refine", {
      method: "POST",
      body: JSON.stringify({
        page_id: pageId,
        parent_generation_id: parentGenerationId,
        instruction
      })
    }),
  approveGeneration: (generationId: number) =>
    apiRequest<Generation>("/generations/approve", {
      method: "POST",
      body: JSON.stringify({ generation_id: generationId })
    }),
  listPageGenerations: (pageId: number) => apiRequest<Generation[]>(`/pages/${pageId}/generations`)
};
