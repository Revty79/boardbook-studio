"use client";

import Link from "next/link";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";

import { api } from "@/lib/api";
import { Character } from "@/lib/types";

export default function CharacterLibraryPage() {
  const params = useParams<{ id: string }>();
  const projectId = useMemo(() => Number(params.id), [params.id]);

  const [characters, setCharacters] = useState<Character[]>([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [personality, setPersonality] = useState("");
  const [lockedTraits, setLockedTraits] = useState("");

  const load = async () => {
    const data = await api.listCharacters(projectId);
    setCharacters(data);
  };

  useEffect(() => {
    if (Number.isFinite(projectId)) {
      void load();
    }
  }, [projectId]);

  const onCreate = async (event: FormEvent) => {
    event.preventDefault();
    await api.createCharacter(projectId, {
      name,
      description,
      personality,
      locked_traits: lockedTraits
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean)
    });
    setName("");
    setDescription("");
    setPersonality("");
    setLockedTraits("");
    await load();
  };

  return (
    <div className="grid gap-5 lg:grid-cols-[360px,1fr]">
      <section className="card p-4">
        <h2 className="mb-3 text-xl font-bold">Add Character</h2>
        <form className="space-y-3" onSubmit={onCreate}>
          <div>
            <label className="label">Name</label>
            <input className="field" value={name} onChange={(event) => setName(event.target.value)} required />
          </div>
          <div>
            <label className="label">Description</label>
            <textarea
              className="field min-h-20"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
            />
          </div>
          <div>
            <label className="label">Personality</label>
            <input className="field" value={personality} onChange={(event) => setPersonality(event.target.value)} />
          </div>
          <div>
            <label className="label">Locked traits (comma-separated)</label>
            <input className="field" value={lockedTraits} onChange={(event) => setLockedTraits(event.target.value)} />
          </div>
          <button className="btn btn-primary w-full">Create Character</button>
        </form>
      </section>

      <section className="card p-4">
        <h2 className="mb-3 text-xl font-bold">Character Library</h2>
        <div className="space-y-3">
          {characters.map((character) => (
            <Link
              key={character.id}
              href={`/projects/${projectId}/characters/${character.id}`}
              className="block rounded-xl border border-[#e5d3b2] bg-white/70 p-3"
            >
              <h3 className="font-bold">{character.name}</h3>
              <p className="label">{character.description || "No description"}</p>
              <p className="mt-1 text-xs text-[#5e4c3e]">
                Locked traits: {character.locked_traits.length ? character.locked_traits.join(", ") : "none"}
              </p>
            </Link>
          ))}
          {characters.length === 0 && <p className="label">No characters yet.</p>}
        </div>
      </section>
    </div>
  );
}
