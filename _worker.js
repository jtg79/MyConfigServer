export default {
  async fetch(request, env) {
    // لینک RAW فایل sub_link.txt خودت را اینجا بگذار
    const githubUrl = "https://raw.githubusercontent.com/jtg79/MyConfigServer/refs/heads/main/sub_link.txt";
    
    const response = await fetch(githubUrl);
    const content = await response.text();
    
    return new Response(content, {
      headers: { 
        "content-type": "text/plain; charset=utf-8",
        "Access-Control-Allow-Origin": "*"
      },
    });
  },
};
