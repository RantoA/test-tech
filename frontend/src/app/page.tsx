import { Container } from "@/components/layout/Container";
import { LatestPostsBanner } from "@/components/posts/LatestPostsBanner";
import { PostBrowser } from "@/components/posts/PostBrowser";

export default function HomePage() {
  return (
    <>
      <LatestPostsBanner />
      <Container className="py-12">
        <PostBrowser />
      </Container>
    </>
  );
}
