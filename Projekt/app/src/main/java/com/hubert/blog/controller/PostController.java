package com.hubert.blog.controller;

import com.hubert.blog.dto.PostResponse;
import com.hubert.blog.model.Post;
import com.hubert.blog.service.PostService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.security.Principal;
import java.util.List;

@RestController
@RequestMapping("/posts")
@RequiredArgsConstructor
public class PostController {
    private final PostService postService;

    @GetMapping
    public List<PostResponse> getPosts(){
        return postService.getAllPosts();
    }

    @PostMapping
    public Post addPost(@RequestBody Post post, Principal principal){
        return postService.addPost(post, principal.getName());
    }

    @DeleteMapping("/{id}")
    public void removePost(@PathVariable long id, Principal principal){
        postService.removePost(id, principal.getName());
    }

}
