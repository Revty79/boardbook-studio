export type Project = {
  id: number;
  title: string;
  description: string | null;
  created_at: string;
};

export type ProjectDetail = Project & {
  stats: {
    character_count: number;
    page_count: number;
    generation_count: number;
  };
};

export type DashboardSummary = {
  project_count: number;
  character_count: number;
  page_count: number;
  generation_count: number;
};

export type CharacterReference = {
  id: number;
  character_id: number;
  image_path: string;
  note: string | null;
  created_at: string;
};

export type Character = {
  id: number;
  project_id: number;
  name: string;
  description: string | null;
  personality: string | null;
  locked_traits: string[];
  created_at: string;
  updated_at: string;
  references: CharacterReference[];
};

export type StyleProfile = {
  id: number;
  project_id: number;
  visual_style: string;
  color_palette: string;
  lighting: string;
  composition: string;
  negative_prompt_rules: string;
  created_at: string;
  updated_at: string;
};

export type StoryPage = {
  id: number;
  project_id: number;
  title: string;
  page_number: number;
  text_content: string;
  approved_generation_id: number | null;
  created_at: string;
  updated_at: string;
};

export type RefinementMessage = {
  id: number;
  generation_id: number;
  role: string;
  content: string;
  created_at: string;
};

export type Generation = {
  id: number;
  page_id: number;
  parent_generation_id: number | null;
  prompt: string;
  negative_prompt: string;
  seed: number | null;
  provider: string;
  image_path: string;
  generation_type: "initial" | "refine" | "variation" | "inpaint" | "mock";
  created_at: string;
  approved_at: string | null;
  refinement_messages: RefinementMessage[];
};
