#include <stdio.h>
#include "ppm.h"
#include <thread>
#include <mutex>

std::mutex mtx;

int image_width = 25000;
int image_height = 20000;
int max_thread_depth = 3;
const char* filename = "dibolt.ppm";

void convert(ushortint magnitude, unsigned char direction, ushortint* xp, ushortint* yp) {
    *xp = magnitude;
    
    if (direction % 2 >= 1) {
        *yp = magnitude;
    }
    else {
        *yp = 0;
    }

    if (direction % 4 >= 2) {
        ushortint swapStorage = *yp;
        *yp = *xp;
        *xp = -swapStorage;
    }

    if (direction % 8 >= 4) {
        *xp = -*xp;
        *yp = -*yp;
    }
}

void populate_buffer(PPM *file, int thread_depth, unsigned int tier, char angle1, bool flip1, char angle2, bool flip2, ushortint speed, unsigned char direction, bool flipped, ushortint x, ushortint y, unsigned char red, unsigned char green, unsigned char blue, std::thread** threads, unsigned int* running_thread_count, unsigned int* ended_thread_count, bool is_thread) {
    //printf("%d %d %d %d %d %d %d %d %d %d\n", tier, angle1, flip1, angle2, flip2, speed, direction, flipped, x, y);
    if (tier <= 0) {
        //printf("%d %d\n", x, y);
        //printf("state1:\nx:%d, y:%d, r:%d, g:%d, b:%d\n\n", x, y, red, green, blue);
        (*file).set_pixel(x, y, red, green, blue);
        //printf("test2");
        (*file).set_pixel(x+1, y, red, green, blue);
        //printf("test3");
        (*file).set_pixel(x, y+1, red, green, blue);
        //printf("test4");
        (*file).set_pixel(x+1, y+1, red, green, blue);
        //printf("test5");
    }
    else {
        //printf("%d\n", direction);
        ushortint delX;
        ushortint delY;
        convert(speed, direction, &delX, &delY);
        ushortint new_speed = speed;
        if (direction % 2 == 0) {
            new_speed = speed / 2;
        }
		
		if (y > image_height - 10) {
			printf("bad y!\n");
		}

        /*if (thread_depth > 0) {
            printf("thread depth:%d, positive:%d\n", thread_depth, thread_depth>0);
        }*/
        if (thread_depth > 0) {
            mtx.lock();
            //printf("%d\n", thread_depth);
            std::thread* new_thread = new std::thread (populate_buffer, file, thread_depth-1, tier-1, angle1, flip1, angle2, flip2, new_speed, direction + (flipped?(-angle1):angle1), flipped != flip1, x + delX, y + delY, red, green, blue, threads, running_thread_count, ended_thread_count, true);
            threads[*running_thread_count] = new_thread;
            *running_thread_count += 1;
            mtx.unlock();
        }
        else {
            populate_buffer(file, thread_depth-1, tier-1, angle1, flip1, angle2, flip2, new_speed, direction + (flipped?(-angle1):angle1), flipped != flip1, x + delX, y + delY, red, green, blue, threads, running_thread_count, ended_thread_count, false);
        }

        populate_buffer(file, thread_depth-1, tier-1, angle1, flip1, angle2, flip2, new_speed, direction + (flipped?(-angle2):angle2), flipped != flip2, x - delX, y - delY, red, green, blue, threads, running_thread_count, ended_thread_count, false);
        if (is_thread) {
            *ended_thread_count += 1;
        }
    }
}

void populate_with_colour(PPM* file, int thread_depth, unsigned int tier, char angle1, bool flip1, char angle2, bool flip2, unsigned char cardinalDir, bool flipped, ushortint x, ushortint y) {
    unsigned int running_thread_count = 0;
    std::thread** threads = new std::thread*[8];
    unsigned int ended_thread_count = 0;

    ushortint speed = 1;
    for (int i=0; i<tier-2; i+=2) {
        speed *= 2;
    }
    unsigned char direction = cardinalDir * 2 + ((tier%2==0)?1:0);
    ushortint delX;
    ushortint delY;
    convert(speed, direction, &delX, &delY);
    ushortint new_speed = speed;
    if (direction % 2 == 0) {
        new_speed = speed / 2;
    }

    /*if (thread_depth > 0) {
        std::thread* new_thread = new std::thread (populate_buffer, file, thread_depth-1, tier-1, angle1, flip1, angle2, flip2, new_speed, direction + (flipped?(-angle1):angle1), flipped != flip1, x + delX, y + delY, 255, 0, 0, threads, &running_thread_count, &ended_thread_count, true);
        mtx.lock();
        threads[running_thread_count] = new_thread;
        running_thread_count += 1;
        mtx.unlock();
    }*/
    //else {
        populate_buffer(file, thread_depth-1, tier-1, angle1, flip1, angle2, flip2, new_speed, direction + (flipped?(-angle1):angle1), flipped != flip1, x + delX, y + delY, 255, 0, 0, threads, &running_thread_count, &ended_thread_count, false);
    //}

    printf("home stretch1!\nthread count:%d, ended:%d\n\n", running_thread_count, ended_thread_count);

    while (ended_thread_count < running_thread_count) {}

    printf("new home stretch1!\nthread count:%d. ended:%d\n\n", running_thread_count, ended_thread_count);

    for (int i=0; i<running_thread_count; i++) {
        //printf("%d", i);
        (*(threads[i])).join();
        //printf("%d\n", i);
    }

    ended_thread_count = 0;
    running_thread_count = 0;

    populate_buffer(file, thread_depth-1, tier-1, angle1, flip1, angle2, flip2, new_speed, direction + (flipped?(-angle2):angle2), flipped != flip2, x - delX, y - delY, 0, 0, 255, threads, &running_thread_count, &ended_thread_count, false);

    printf("home stretch2!\nthread count:%d, ended:%d\n\n", running_thread_count, ended_thread_count);

    while (ended_thread_count < running_thread_count) {}

    printf("new home stretch2!\nthread count:%d. ended:%d\n\n", running_thread_count, ended_thread_count);

    for (int i=0; i<running_thread_count; i++) {
        //printf("%d", i);
        (*(threads[i])).join();
        //printf("%d\n", i);
    }
    //printf("end\n\n");
}

int main(int argc, char** argv) {
    PPM file;
    file.set_dimensions(image_width, image_height);
    file.allocate();
    populate_with_colour(&file, max_thread_depth, 25, 1, true, 3, true, 0, false, 11000,10000);
    //printf("out\n\n")
    file.save_to_file(filename);
    //printf("true end\n");
    return 0;
}