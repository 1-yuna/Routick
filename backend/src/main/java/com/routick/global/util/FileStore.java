package com.routick.global.util;

import com.routick.global.exception.CustomException;
import com.routick.global.exception.ErrorCode;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.multipart.MultipartFile;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;

// 업로드 파일을 로컬 디스크에 저장하고 접근 URL을 반환
@Component
public class FileStore {

    @Value("${file.upload-dir}")
    private String uploadDir;

    public String save(MultipartFile file) {
        try {
            String filename = UUID.randomUUID() + "_" + file.getOriginalFilename();
            Path dir = Paths.get(uploadDir).toAbsolutePath();
            Files.createDirectories(dir);
            file.transferTo(dir.resolve(filename).toFile());
            return "/images/" + filename;   // 아래 WebConfig 매핑으로 접근
        } catch (Exception e) {
            throw new CustomException(ErrorCode.IMAGE_UPLOAD_FAILED);
        }
    }
}