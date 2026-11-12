import { Container } from "@/components/layout/Container";
import { Hero } from "@/components/layout/Hero";
import { PostBrowser } from "@/components/posts/PostBrowser";

export default function HomePage() {
  return (
    <>
      <Hero />
      <Container className="py-12">
        <PostBrowser />
      </Container>
    </>
  );
}
