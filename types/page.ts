export interface PageProps {
  params: Promise<{ id: string }> | { id: string };
}

