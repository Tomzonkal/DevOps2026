package com.hubert.blog.service;

import com.hubert.blog.dto.PostResponse;
import com.hubert.blog.model.Post;
import com.hubert.blog.model.User;
import com.hubert.blog.repository.PostRepository;
import com.hubert.blog.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class PostService {
    private final PostRepository postRepository;
    private final UserRepository userRepository;

    public List<PostResponse> getAllPosts(){
        return postRepository.findAll().stream().map(this::mapToResponse).collect(Collectors.toList());
    }

    private PostResponse mapToResponse(Post post) {
        return PostResponse.builder()
                .id(post.getId())
                .title(post.getTitle())
                .content(post.getContent())
                .authorName(post.getOwner() != null ? post.getOwner().getUsername() : "Anonim")
                .build();
    }

    public Post addPost(Post post, String username){
        User user = userRepository.findByUserName(username).orElseThrow(()->new UsernameNotFoundException("User not found"));

        post.setOwner(user);

        return postRepository.save(post);
    }

    public void removePost(long id, String username){
        Post post = postRepository.findById(id).orElseThrow(()->new RuntimeException("Post not found"));

        if (post.getOwner() == null || ! post.getOwner().getUsername().equals(username)) {
            throw new RuntimeException("You cannot delete this post!");
        }

        postRepository.delete(post);
    }
}
