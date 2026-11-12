import { Container } from "./Container";

export function Footer() {
  return (
    <footer className="mt-auto border-t border-line bg-surface">
      <Container className="flex flex-col gap-2 py-6 text-xs text-muted sm:flex-row sm:items-center sm:justify-between">
        <span>© {new Date().getFullYear()} my-blog — Blog Post Manager</span>
        <span>Built with FastAPI, PostgreSQL and Next.js</span>
      </Container>
    </footer>
  );
}
