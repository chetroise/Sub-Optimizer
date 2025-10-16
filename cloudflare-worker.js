export default {
  async fetch(request, env) {
    // --- Token 验证逻辑 ---
    const SECRET_TOKEN = env.AUTH_TOKEN;
    const url = new URL(request.url);
    const clientToken = url.searchParams.get('token');

    if (!clientToken || clientToken !== SECRET_TOKEN) {
      return new Response('Forbidden: Invalid token', { status: 403 });
    }
    // --- Token 验证结束 ---

    const GITHUB_TOKEN = env.GITHUB_TOKEN;
    const GITHUB_USER = env.GITHUB_USER;
    const GITHUB_REPO = env.GITHUB_REPO;
    const FILE_PATH = 'optimized_config.json';
    const githubUrl = `https://api.github.com/repos/${GITHUB_USER}/${GITHUB_REPO}/contents/${FILE_PATH}`;

    // 定义请求 GitHub 的 fetch 选项，并开启5分钟缓存
    const init = {
      headers: {
        'Accept': 'application/vnd.github.raw',
        'Authorization': `token ${GITHUB_TOKEN}`,
        'User-Agent': 'Cloudflare-Worker'
      },
      cf: {
        cacheTtl: 300, // 缓存300秒 = 5分钟
        cacheEverything: true,
      }
    };

    try {
      const response = await fetch(githubUrl, init);

      if (!response.ok) {
        const errorText = await response.text();
        return new Response(`Error fetching from GitHub: ${response.status} ${response.statusText}\n${errorText}`, { status: response.status });
      }

      const newHeaders = new Headers(response.headers);
      newHeaders.set('Content-Type', 'application/json;charset=UTF-8');
      // 清理掉一些 GitHub 特有的、不需要暴露给客户端的头信息
      newHeaders.delete('x-github-request-id');
      newHeaders.delete('access-control-allow-origin');

      return new Response(response.body, {
        status: response.status,
        headers: newHeaders
      });

    } catch (e) {
      return new Response(`Worker Error: ${e.message}`, { status: 500 });
    }
  },
};
