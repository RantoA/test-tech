import { Container } from "@/components/layout/Container";
import { ButtonLink } from "@/components/ui/Button";

export default function NotFound() {
  return (
    <Container className="py-24 text-center">
      <p className="text-sm font-medium text-accent">404</p>
      <h1 className="mt-2 text-2xl font-semibold text-ink">Page not found</h1>
      <p className="mt-2 text-sm text-muted">The page you are looking for does not exist.</p>
      <ButtonLink href="/" variant="secondary" className="mt-8">
        Back to articles
      </ButtonLink>
    </Container>
  );
}
